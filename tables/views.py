from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .functions.ConvertSums import CreateSUMS
import pandas as pd
from .models import SUMS
# Create your views here.


"""A view to upload SUMS data from grantees"""
class UploadSums(APIView):
    def post(self,request):
      grantee=request.POST.get('grantee')
      quota=request.POST.get('quota')
      year=request.POST.get('year')
      file=request.FILES.get('file')

      print(grantee)
      processedCSV=CreateSUMS(grantee,file)

      for key in processedCSV:
         print(type(str(key)))
         data=str(key).split('_')
         sums=SUMS(grantee=data[1],quota=data[2],year=int(data[3]))
         sums.file=processedCSV[key]
         sums.file.name=f'{key}.csv'
         sums.save()
      
      response=Response({"csv_data":processedCSV}, content_type='text/csv')
      response['Content-Disposition'] = 'attachment; filename="file"'
      return response

      
class getSUMS(APIView):
   def post(self,request):
      column=request.POST.get('code')
      district=request.POST.get('district')
      grantee=request.POST.get('grantee')
      quota=request.data.get('quota')
      year=request.data.get('year')
      print(grantee)

      try:
         data=SUMS.objects.get(grantee=grantee,quota=quota,year=year)
         print(data)
         df=pd.read_csv(data.file.path)

         #Drop null values
         df.dropna(inplace=True)
         # print(df.head())

         filtered_df=df[['district',column]]
         print(filtered_df.head())
         return Response({'success':True},status=status.HTTP_200_OK)
      except SUMS.DoesNotExist:
         return Response({'success':False},status=status.HTTP_404_NOT_FOUND)
      return ""



