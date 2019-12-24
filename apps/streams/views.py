from django.http import HttpResponse
from django.utils.timezone import now
from django.views import View

from .models import Stream, Distribution


class OnPublishStartView(View):
    def post(self, request):
        """
        Triggered by nginx-rtmp when a stream starts.
        """
        stream: Stream = Stream.objects.create(
            status="live",
            app=request.POST['app'],
            key=request.POST['name'],
            flash_version=request.POST['flashver'],
            swf_url=request.POST['swfurl'],
            tcurl=request.POST['tcurl'],
            page_url=request.POST['pageurl'],
            client_id=int(request.POST['clientid']),
            source_ip=request.POST['addr'],
            started=now())

        print(f"Started stream {stream.id} from /{stream.app}/{stream.key}")
        return HttpResponse()


class OnPublishDoneView(View):
    def post(self, request):
        """
        Triggered by nginx-rtmp when a stream stops.
        """
        stream: Stream = Stream.objects.get(
            app=request.POST['app'],
            key=request.POST['name'],
            status="live")
        stream.status = "finished"
        stream.stopped = now()
        stream.save()

        print(f"Stopped stream {stream.id} from /{stream.app}/{stream.key}")
        return HttpResponse()


class OnDistributionStartView(View):
    def post(self, request):
        """
        Triggered by nginx-rtmp when a distribution of a stream starts.
        """
        key = request.POST['name'].split("__")[0]
        stream: Stream = Stream.objects.get(
            key=key,
            status="live")

        distribution_key: str = request.POST['name'].split("__")[1]
        distribution, _ = Distribution.objects.get_or_create(
            stream=stream,
            name=distribution_key.title(),
            key=distribution_key)

        return HttpResponse()


class OnDistributionDoneView(View):
    def post(self, request):
        """
        Triggered by nginx-rtmp when a distribution of a stream stops.
        """
        return HttpResponse()