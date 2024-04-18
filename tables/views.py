import os
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .functions.ConvertSums import CreateSUMS
from .functions.computeAT import compute_annual_totals
from .functions.computeCT import compute_cumulative_totals
import pandas as pd
from .models import SUMS,AnnualTotals,CummulativeTotals
import ast
# Create your views here.

def saveTotals(grantee,start_year,end_year,at_file):
   try:
      data=AnnualTotals.objects.get(grantee=grantee.casefold(),year=f'{start_year}{end_year}')
      os.remove(data.file.path)
      data.delete()
      data=AnnualTotals(grantee=grantee.casefold(),year=f"{start_year}{end_year}")
      data.file=at_file
      data.file.name=f'at_{grantee}_{start_year}{end_year}.csv'.casefold()
      data.save()
      return os.path.dirname(data.file.path)
         

   except AnnualTotals.DoesNotExist:
      data=AnnualTotals(grantee=grantee.casefold(),year=f"{start_year}{end_year}")
      data.file=at_file
      data.file.name=f'at_{grantee}_{start_year}{end_year}.csv.'.casefold()
      data.save()
      return os.path.dirname(data.file.path)

""""
   Function to store cummulative totals from annual totals
"""
def saveCT(grantee,file):
   try:
      data=CummulativeTotals.objects.get(grantee=grantee.casefold())
      os.remove(data.file.path)
      data.delete()
      data=CummulativeTotals(grantee=grantee.casefold())
      data.file=file
      data.file.name=f"ct_{grantee}.csv".casefold()
      data.save()
      return os.path.dirname(data.file.path)
   
   except CummulativeTotals.DoesNotExist:
      data=CummulativeTotals(grantee=grantee.casefold())
      data.file=file
      data.file.name=f"ct_{grantee}.csv".casefold()
      data.save()
      return os.path.dirname(data.file.path)


"""
   A view to upload SUMS data from grantees from a setup frontend
"""
class UploadSums(APIView):
    def post(self,request):
      grantee=request.POST.get('grantee')
      quota=request.POST.get('quota')
      year=request.POST.get('year')
      file=request.FILES.get('file')
      path=''
      atpath=''
      
      print('uploading SUMS')
      processedCSV=CreateSUMS(grantee,file)

      for key in processedCSV:
         # print(type(str(key)))
         data=str(key).split('_')
         year=int(data[3])
         # grantee=data[1]
         try:
            sumsdata=SUMS.objects.get(grantee=data[1],quota=data[2],year=int(data[3]))
            os.remove(sumsdata.file.path)
            sumsdata.delete()
            sums=SUMS(grantee=data[1],quota=data[2],year=int(data[3]))
            sums.file=processedCSV[key]
            sums.file.name=f'{key}.csv'
            sums.save()
            path=os.path.dirname(sums.file.path)
         except SUMS.DoesNotExist:
            sums=SUMS(grantee=data[1],quota=data[2],year=int(data[3]))
            sums.file=processedCSV[key]
            sums.file.name=f'{key}.csv'
            sums.save()
            path=os.path.dirname(sums.file.path)
         

         # previous_year=int(year)-1
         # next_year=int(year)+1
      years_list=[]
      for filename in os.listdir(path):
         if filename.endswith(".csv") and filename.startswith(f"sums_{grantee}".casefold()):# Check if the file is a CSV and starts with "sums_"
            # Extract the year from the filename
            year = int(filename.split("_")[-1].split(".")[0])  # Extracting the year from the filename
            years_list.append(year)
            
      print(years_list)
      print('Computing Annual totals')
      for year in range(min(years_list),max(years_list)+2):
         try:
            annual_totals=compute_annual_totals(path,grantee,year-1,year)
            atpath=saveTotals(grantee,year-1,year,annual_totals)
         except TypeError as e:
            if "'NoneType' object is not iterable" in e.args[0]:
               print(f'A for {year-1}-{year} was not found')
         
      

      # store cummulative totals
      print('Computing Cummulative Totals')
      cummulative_totals=compute_cumulative_totals(atpath,grantee)
      saveCT(grantee,cummulative_totals)

      response=Response({"csv_data":processedCSV}, content_type='text/csv')
      response['Content-Disposition'] = 'attachment; filename="file"'
      return response



class computeTotals(APIView):
   def post(self,request):
      grantee=request.data.get('grantee')
      start_year=request.data.get('start_year')
      end_year=request.data.get('end_year')

      
      sumsdata=SUMS.objects.filter(grantee=grantee, year=start_year)
      if sumsdata.exists():
         sumsobject=sumsdata.first()
         sumspath=os.path.dirname(sumsobject.file.path)

         annual_totals=compute_annual_totals(sumspath,grantee,start_year,end_year)

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

      sumsdata=[]
      try:
         data=SUMS.objects.get(grantee=grantee,quota=quota,year=year)
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

class getAT(APIView):
   def post(self, request):
      grantee=request.data.get('grantee')
      year=request.data.get('year')
      column=request.data.get('code')
      print(grantee)
      atdata=[]

      try:
         data=AnnualTotals.objects.get(grantee=grantee,year=year)
         df=pd.read_csv(data.file.path)
         df.dropna(inplace=True)

         #filter the dataframe
         filtered_df=df[['district',column]]
         
         for index, row in filtered_df.iterrows():
            col=ast.literal_eval(row[column])
            print(col)
            try:
               objectStruct={
                  'district':row['district'],
                  'totalQ1':col['TotalQ1'],
                  'totalQ2':col['TotalQ2'],
                  'totalQ3':col['TotalQ3'],
                  'totalQ4':col['TotalQ4'],
                  'annualtotal':col['AnnualTotal']
               }
            
            except KeyError as e:
               # print(f"Error: {e.args}\n\n")
               print(f"KeyError: The key '{e.args[0]}' is not found in the dictionary.")
               objectStruct={
                  'district':row['district'],
                  'totalQ1':col['TotalQ1'],
                  'totalQ2':col['TotalQ2'],
                  'totalQ3':col['TotalQ3'],
                  'annualtotal':col['AnnualTotal']
               }
            atdata.append(objectStruct)
         return Response({'success':True,'data':atdata},status=status.HTTP_200_OK)
      except AnnualTotals.DoesNotExist:
         return Response({'success':False},status=status.HTTP_404_NOT_FOUND)



class getCT(APIView):
   def post(self,request):
      grantee=request.data.get('grantee')
      column=request.data.get('code')

      try:
         data=CummulativeTotals.objects.get(grantee=grantee)
         df=pd.read_csv(data.file.path)
         df.dropna(inplace=True)
         ct_data=[]
         #filter the dataframe
         filtered_df=df[['district',column]]

         for index, row in filtered_df.iterrows():
            col=ast.literal_eval(row[column])
            print(col)
            objectStruct={
                  'annualtotaly1':col['AnnualTotalY1'],
                  'annualtotaly2':col['AnnualTotalY2'],
                  'annualtotaly3':col['AnnualTotalY3'],
                  'cummulativetotal':col['CummulativeTotal']
               }
            ct_data.append(objectStruct)

         return Response({'success':True,'data':ct_data},status=status.HTTP_200_OK)
      
      except CummulativeTotals.DoesNotExist:
         return Response({'success':True},status=status.HTTP_404_NOT_FOUND)