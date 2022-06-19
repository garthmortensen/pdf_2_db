```none
GM###  #####  ######    #    # # #    # ###### #####
#    # #    # #         ##  ## # ##   # #      #    #
#    # #    # #####     # ## # # # #  # #####  #    #
#####  #    # #         #    # # #  # # #      #####
#      #    # #         #    # # #   ## #      #   #
#      #####  #         #    # # #    # ###### #    #
```



The goal of this code is to:

1. Using OCRmyPDF on Red Hat, OCR some pdfs and extract content as txt.
2. process all *.txt.
3. load txt into db, with meaningful table relationships which link pdf metadata and content to the keywords which they contain.



Improvements:

1. Use SQLAlchemy.
2. Convert to classes and modularize.
3. Depending on size of pdf content, maybe refactor so that pdfs are processed and inserted into db table one file at a time. If there were 100 gigs of pdf content to load, memory would be an issue.
4. Add more functionality to the `string_cleaning` process.
5. Rewrite for whatever use case.
