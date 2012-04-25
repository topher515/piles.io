from django.db.models import Q

from tastypie.authentication import Authentication
from tastypie.authorization import Authorization


class ShinyboxAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if 'daniel' in request.user.username:
          return True

        return False

    # Optional but recommended
    def get_identifier(self, request):
        return request.user.username




class FilesAuthorization(Authorization):
    def is_authorized(self, request, object=None):
        return True

    # Optional but useful for advanced limiting, such as per user.
    def apply_limits(self, request, object_list):
        
        if request.user.is_authenticated():
            if request.method == 'DELETE':
                # Only can delete files for which you are the bucket admin
                return object_list.filter(bucket__admin=request.user)  
            if request.method == 'GET':
                # Only can see files for which you are admin
                return object_list.filter(Q(bucket__admin=request.user)) # TODO: Allow user to files he's uploaded
        
        return object_list.none()