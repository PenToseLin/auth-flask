#
# from App.model.user import User
#
#
# class JWToken(JWT):
#     @staticmethod
#     @JWT.authentication_handler()
#     def authenticate(username, password):
#         user_info = User.query.filter_by(username=username).first()
#         return user_info
#
#     @staticmethod
#     @JWT.identity_handler()
#     def identity(payload):
#         user = payload['identity']
#         return User.get(user.id)
