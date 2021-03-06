from django.shortcuts import render,get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from  .models import Review,Wine,Cluster
from .forms import ReviewForm
from .suggestions import update_clusters
import datetime

# Create your views here.

def review_list(request):
    #get a list of the latest 9 reviews and renders it using 'reviews/list.html' 
    latest_review_list=Review.objects.order_by('-pub_date')[:9]
    context={'latest_review_list':latest_review_list}
    return render(request,'reviews/review_list.html',context) 

def review_detail(request,review_id):
    #get a review given its ID and renders it using review_detail.html
    review=get_object_or_404(Review,pk=review_id)
    return render(request,'reviews/review_detail.html',{'review':review})

def wine_list(request):
    #get all the wines sorted by name and passes it to wine_list.html
    wine_list=Wine.objects.order_by('-name')
    context={'wine_list':wine_list}
    return render(request,'reviews/wine_list.html',context)

def wine_detail(request,wine_id):
    #get a wine from the DB given its ID and renders it using wine_detail.html
    wine=get_object_or_404(Wine,pk=wine_id)
    return render(request,'reviews/wine_detail.html',{'wine':wine})

@login_required
def add_review(request,wine_id):
    #use the request url wine ID to look for the wine we are going to add the review to. 
    #it will redirect the view to a 404 page if it doesn't find it  
    wine=get_object_or_404(Wine,pk=wine_id) 
    #create a ReviewForm instance from the request POST data
    form = ReviewForm(request.POST)
    if form.is_valid():
        rating=form.cleaned_data['rating']
        comment=form.cleaned_data['comment']
        #user_name=form.cleaned_data['user_name']
        user_name=request.user.username
        review=Review()
        review.wine=wine
        review.user_name=user_name
        review.rating=rating
        review.comment=comment
        review.pub_date=datetime.datetime.now()
        review.save()
        update_clusters()
        #Always return an HttpResponseRedirect after successfully dealing
        #with POST data. This prevents data from being posted twice if a 
        #user hits the Back button.
        return HttpResponseRedirect(reverse('reviews:wine_detail',args=(wine.id,)))

    return render(request,'reviews/wine_detail.html',{'wine':wine,'form':form})


def user_review_list(request,username=None):
    if not username:
        username=request.user.username
    latest_review_list=Review.objects.filter(user_name=username).order_by('-pub_date')
    context={'latest_review_list':latest_review_list,'username':username}
    return render(request,'reviews/user_review_list.html',context)

@login_required
def user_recommendation_list(request):
    #get this user reviews
    user_reviews=Review.objects.filter(user_name=request.user.username).prefetch_related('wine')
    #from the reviews, get a set of wine IDs
    user_reviews_wine_ids=set(map(lambda x: x.wine.id,user_reviews))
    
    #get request user cluster name (just the first one right now)
    try:
        user_cluster_name=\
            User.objects.get(username=request.user.username).cluster_set.first().name
    except: #if no cluster has been assigned for a user, update clusters
        update_clusters()
        user_cluster_name=\
            User.objects.get(username=request.user.username).cluster_set.first().name
        

    #get usernames for other members of the cluster 
    user_cluster_other_members=\
        Cluster.objects.get(name=user_cluster_name).users.exclude(username=request.user.username).all()
    other_members_usernames=set(map(lambda x: x.username, user_cluster_other_members))

    #get reviews by those users, excluding wines reviewed by the request user
    other_users_reviews=\
        Review.objects.filter(user_name__in=other_members_usernames).exclude(wine__id__in=user_reviews_wine_ids)
    other_users_reviews_wine_ids=set(map(lambda x: x.wine.id,other_users_reviews))

    #then get a wine list excluding the previous IDs, order by rating
    wine_list=sorted(list(Wine.objects.filter(id__in=other_users_reviews_wine_ids)),key=lambda x: x.average_rating,reverse=True)

    return render(request,'reviews/user_recommendation_list.html',{'username':request.user.username,'wine_list':wine_list})

