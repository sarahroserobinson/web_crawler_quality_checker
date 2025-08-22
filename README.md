# web_crawler_quality_checker


## Introduction to the project

This project creates a Web Crawler that crawls a domain to complete a quality assessment of each page crawled. It gathers data and metrics which are exported in csv or json formats and designed to integrate with Grafana dashboards. 

Data collected:


## Requirements
Python 3
Libraries:
* requests
* beautifulsoup4

## How to use

``` 
python crawler.py
```
Or use it in a script:

```
python
Copy
Edit
quality_checker = WebPageReport("https://example.com", 10, "json")
quality_checker.run()
quality_checker.export_as_csv()
quality_checker.export_as_json()
```

The output is saved to:

```
Quality-Report-<domain>-<date>.csv
Quality-Report-<domain>-<date>.json
```


