from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)


@method_decorator(login_required, name='dispatch')
class APIView(SpectacularAPIView):
    pass


@method_decorator(login_required, name='dispatch')
class SwaggerView(SpectacularSwaggerView):
    pass


@method_decorator(login_required, name='dispatch')
class RedocView(SpectacularRedocView):
    pass
