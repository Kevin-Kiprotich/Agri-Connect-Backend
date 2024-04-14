import os
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .functions.ConvertSums import CreateSUMS
from .functions.computeAT import compute_annual_totals
import pandas as pd
from .models import SUMS,AnnualTotals
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

class computeTotals(APIView):
   def post(self,request):
      grantee=request.data.get('grantee')
      start_year=request.data.get('start_year')
      end_year=request.data.get('end_year')

      
      sumsdata=SUMS.objects.filter(grantee=grantee, year=start_year)
      print(sumsdata.exists())

      if sumsdata.exists():
         sumsobject=sumsdata.first()
         sumspath=os.path.dirname(sumsobject.file.path)

         annual_totals=compute_annual_totals(sumspath,grantee,start_year,end_year)
         print(annual_totals)

         try:
            data=AnnualTotals.objects.get(grantee=grantee,year=f'{start_year}{end_year}')
            os.remove(data.file.path)
            data.delete()
            data=AnnualTotals(grantee=grantee,year=f"{start_year}{end_year}")
            data.file=annual_totals
            data.file.name=f'at_{grantee}_{start_year}{end_year}.csv'
            data.save()
            return Response({'success':True,'message':'Annual Totals object found'},status=status.HTTP_200_OK)
         
         except AnnualTotals.DoesNotExist:
            data=AnnualTotals(grantee=grantee,year=f"{start_year}{end_year}")
            data.file=annual_totals
            data.file.name=f'at_{grantee}_{start_year}{end_year}.csv'
            data.save()
            return Response({'success':True,'message':'Annual Totals object not found. New object created'},status=status.HTTP_200_OK)
         
      else:
         return Response({'success':False,'message':'SUMS object not Found'})


'''
   Function to fetch SUMS from the database to frontend.
'''
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



