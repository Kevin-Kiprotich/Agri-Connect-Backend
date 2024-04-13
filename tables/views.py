from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .functions.ConvertSums import CreateSUMS
import pandas as pd
from .models import SUMS
import ast
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
      grantee=request.data.get('grantee')
      quota=request.data.get('quota')
      year=request.data.get('year')
      column=request.data.get('code')
      print(grantee)

      sumsdata=[]
      try:
         data=SUMS.objects.get(grantee=grantee,quota=quota,year=year)
         print(data)
         df=pd.read_csv(data.file.path)

         #Drop null values
         df.dropna(inplace=True)
         # print(df.head())

         filtered_df=df[['district',column]]
         
         for index, row in filtered_df.iterrows():
            col=ast.literal_eval(row[column])
            print(col)
            objectStruct={
               'district':row['district'],
               'adult_male':col["Adult_Male"],
               'adult_female':col["Adult_Female"],
               'youth_male':col["Youth_Male"],
               'youth_female':col["Youth_Female"],
               'reference':col["Reference"],
               'total':col["Total"],
            }
            sumsdata.append(objectStruct)

         
         return Response({'sucess':True,'data':sumsdata},status=status.HTTP_200_OK)
      except SUMS.DoesNotExist:
         return Response({'success':False},status=status.HTTP_404_NOT_FOUND)
      return ""



