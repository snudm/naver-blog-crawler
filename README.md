# Naver Blog Lists Crawler

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

# Naver Blog Texts Crawler

크롤링 전략은 다음과 같다.

1. 블로그 본문 크롤링: 'http://m.blog.naver.com/%s/%s' % (blog_id, log_no)
    - `blogId`: 게시된 블로그의 아이디
    - `logNo`: 게시된 블로그의 고유 숫자
    
    * 종종 비공개 혹은 삭제된 post가 존재함  

## Requirements

- Python 2.7+
- `pip install beautifulsoup4`

## Run

- **input 변수**: category, path, date
	- category: 5 ~ 36까지 총 32개의 category
	- path: base directory로 지정할 경로설정
	- date: 기존에 긁어온 lists에서 본문(texts)을 가져올 날짜 지정
- **output**: json으로 저장된 파일(크롤러가 돌아갈때마다 하나의 파일을 생성하여 저장함)
	- 저장된 objects: blogId, logNo, contentHtml, content, crawledTime, crawlerVersion, categoryName, sympathyCount, images, tags, title, url, wirttenTime
    $ python blog_page_crawler.py --help

## 파일 저장 형태

- crawler version 0.1: `texts/directoryseq/year/month/day/blogId-logNo.json`

## Author

- [Misuk Kim](http://github.com/misuke88)

# Naver Blog Comments Crawler

크롤링 전략은 다음과 같다.

1. 블로그 덧글 크롤링: 'http://m.blog.naver.com/CommentList.nhn?blogId=%s&logNo=%s' % (blog_id, log_no)
    - `blogId`: 게시된 블로그의 아이디
    - `logNo`: 게시된 블로그의 고유 숫자
    
    * 종종 비공개 혹은 삭제된 post가 존재함  

## Requirements

- Python 2.7+
- `pip install beautifulsoup4`

## Run

- **input 변수**: category, path, date
	- category: 5 ~ 36까지 총 32개의 category
	- path: base directory로 지정할 경로설정
	- date: 기존에 긁어온 lists에서 본문(texts)을 가져올 날짜 지정
- **output**: json으로 저장된 파일(크롤러가 돌아갈때마다 하나의 파일을 생성하여 저장함)
	- 저장된 objects: blogId, logNo, comments, commentCrawledTime, wirttenTime
    $ python blog_comment_crawler.py --help

## 파일 저장 형태

- crawler version 0.1: `comments/directoryseq/year/month/day/blogId-logNo.json`

## Author

- [Misuk Kim](http://github.com/misuke88)