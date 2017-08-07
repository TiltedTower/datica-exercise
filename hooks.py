import falcon
import jwt

# Determines existence and validity of session token
def validateToken(req, resp, resource, params):
    cookies = req.cookies
    if 'datica_session' in cookies:
        try:
            sessionToken = cookies['datica_session']
            req.context['username'] = jwt.decode(sessionToken, 'datica')['username']
        except:
            req.context['username'] = None
    else:
        req.context['username'] = None


# Determines authorization level for user CRUD
def authorizeUser(req, resp, resource, params):
    tokenUsername = req.context['username']

    if tokenUsername == params['username']:
        req.context['auth'] = True
    else:
        raise falcon.HTTPUnauthorized()
