import sys, os
import pandas as pd
import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE","winerama.settings")

import django
django.setup()

from reviews.models import Review, Wine

def save_review_from_row(review_row):
    review=Review()
    review.id=review_row[0]
    review.user_name=review_row[1]
    # we use the wine id to look for the wine instance
    # this means that we need to load wines before we load reviews
    review.wine=Wine.objects.get(id=review_row[2])
    review.rating=review_row[3]
    review.pub_date=datetime.datetime.now()
    review.comment=review_row[4]
    review.save()


#the main function for the script, called by the shell
if __name__ =="__main__":
    #check number of arguments (including the command name)
    if len(sys.argv)==2:
        print "Reading from file"+str(sys.argv[1])
        reviews_df=pd.read_csv(sys.argv[1])
        print reviews_df

        #apply save_Review_from_row to each review in the data frame
        reviews_df.apply(
            save_review_from_row,
            axis=1 #(per row)
        )
        
        print "There are {} reviews in DB".format(Review.objects.count())
        
    else:
        print "Please, provide Reviews file path"
