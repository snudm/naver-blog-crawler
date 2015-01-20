# Naver Blog Crawler

크롤링 전략은 다음과 같다.

1. 블로그 크롤링: http://section.blog.naver.com/sub/PostListByDirectory.nhn?option.page.currentPage=1&option.templateKind=0&option.directorySeq=5&option.viewType=default&option.orderBy=date&option.latestOnly=0
    - `currentPage`: 1 ~ 100 page의 블로그 페이지. 한 page에 10개의 blog의 리스트가 존재함
    - `directoryseq`: 5 ~ 36까지의 category로 구성됨. (`category` 옵션을 이용해 입력)
        ex) 5: "문학, 책", 6:"영화" (`section_information.json` 참고)
    - `latestOnly`: binary 변수. 1= 주목받는 글, 0= 전체 글 (`latest-only` 또는 `type` 옵션을 이용해 입력)
    
    * 각 directory별로 12시간 내의 블로그를 가지고 있음 

## Requirements

- Python 2.7+
- `pip install beautifulsoup4`

## Run

- **input 변수**: category, crawler version, type
- **output**: json으로 저장된 파일(크롤러가 돌아갈때마다 하나의 파일을 생성하여 저장함)
	- 저장된 objects: blogId, blogName, content, crawledTime, crawlerVersion, images, logNo, tags, title, url, wirttenTime
    $ python crawler.py --help

## 파일 저장 형태

- crawler version 0.1: `data/directoryseq/year/month/day/*.json`

## Author

- [Misuk Kim](http://github.com/misuke88)
