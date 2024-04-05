from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .functions.ConvertSums import CreateSUMS
# Create your views here.


"""A view to upload SUMS data from grantees"""
class UploadSums(APIView):
    def post(self,request):
      grantee=request.POST.get('grantee')
      file=request.FILES.get('file')

      print(grantee)
      processedCSV=CreateSUMS(file)
      response=Response({"csv_data":processedCSV}, content_type='text/csv')
      response['Content-Disposition'] = 'attachment; filename="file"'
      return response

      




