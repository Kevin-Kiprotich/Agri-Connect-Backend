# AGRICONNECT DJANGO BACKEND

## Uploading Sums Data
Make a post request to SERVER_URL/api/sums/. The payload should be in this format. 

```
{
  "file": file,
  "grantee": grantee name,
"quota": quota,
"year": year
}
```

This will compute the SUMS data, annual totals, and cumulative totals and upload the results to supabase.
