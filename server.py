import falcon
import json
import logging
import database as db 
import hooks
import credentials


class BaseResource:
    @falcon.before(hooks.validateToken)
    def on_get(self, req, resp):
        tokenUsername = req.context['username']
        
        if tokenUsername is not None:
            user = db.find_by_username(tokenUsername)
            resp.body = json.dumps(user)
        else:
            resp.body = json.dumps({ 'Hello': 'World' })



class RegisterResource:
    def on_post(self, req, resp):
        # requires request body to contain username/password, optional info field
        body = json.load(req.stream)
        newUser = db.create_new_user(body)
        
        if newUser is not None:
            newUsername = { 'username': newUser['username'] }
            sessionToken = credentials.generateToken(newUsername)
            resp.set_cookie('datica_session', sessionToken, secure=False, domain='localhost')
            resp.body = json.dumps(newUser)
        else:
            raise falcon.HTTPBadRequest('Invalid Request', 'Username/Password is invalid')

class AuthResource:
    def on_post(self, req, resp):
        body = json.load(req.stream)
        username = body['username']
        reqPassword = body['password']
        user = db.find_by_username(username)

        if user is not None:
            hashedPassword = user['password']
            validLogin = credentials.validatePassword(reqPassword, hashedPassword)

            if validLogin:
                sessionToken = credentials.generateToken({ 'username': username })
                resp.set_cookie('datica_session', sessionToken, secure=False, domain='localhost')
                resp.body = json.dumps({'Success': 'Login Successful'})
            else:
                raise falcon.HTTPBadRequest('Invalid Request', 'Username/Password is invalid')
        else:
            raise falcon.HTTPBadRequest('Invalid Request', 'Username/Password is invalid')

    def on_delete(self, req, resp):
        resp.unset_cookie('datica_session')
        resp.body = json.dumps({ 'Status': 'Successful logout' })



@falcon.before(hooks.validateToken)
@falcon.before(hooks.authorizeUser)
class UserResource:      
    def on_get(self, req, resp, username):
        if req.context['auth']:
            user = db.find_by_username(username)
            resp.body = json.dumps(user)
    
    def on_put(self, req, resp, username):
        body = json.load(req.stream)
        tokenUsername = req.context['username']
        updatedUser = db.update_user(tokenUsername, body['info'])
        resp.body = json.dumps(updatedUser)

    def on_delete(self, req, resp, username):
        tokenUsername = req.context['username']
        db.delete_user(tokenUsername)
        resp.body = json.dumps({'Success': 'User record deleted'})



api = falcon.API()
api.add_route('/', BaseResource())
api.add_route('/auth', AuthResource())
api.add_route('/user', RegisterResource())
api.add_route('/user/{username}', UserResource())
