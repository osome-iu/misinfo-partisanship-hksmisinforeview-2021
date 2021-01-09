python $C/v2/strip_dataset.py $D/misinfo-and-news-tweets $D/stripped-dataset
python $C/v2/remove_bots.py $D/stripped-dataset $D/bot-scores.tab $D/stripped-dataset-no-bots.json

python $C/v2/compute_pollution.py $D/stripped-dataset-no-bots $D/sources/misinfo.tab $D/measures/pollution.tab
python $C/v2/compute_partisanship.py $D/stripped-dataset-no-bots $D/sources/news.tab $D/measures/partisanship.tab

python $C/v2/create_congress_dataset.py $D/congress/ideology-senate.csv $D/congress/twitter-uids-senate.csv $D/senate.tab
python $C/v2/compute_ideology.py $D/stripped-dataset-no-bots $D/senate.tab $D/measures/ideology.tab

python $C/v2/compute_similarities.py $D/stripped-dataset-no-bots $D/similarities.json
python $C/v2/compute_bubbliness.py $D/similarities.json $D/measures/bubbliness.tab

python $C/v2/compute_friend_measures.py $D/measures/pollution.tab $D/friends-reduced.json $D/measures/friends-pollution.tab
python $C/v2/compute_friend_measures.py $D/measures/partisanship.tab $D/friends-reduced.json $D/measures/friends-partisanship.tab
python $C/v2/compute_friend_measures.py $D/measures/ideology.tab $D/friends-reduced.json $D/measures/friends-ideology.tab
python $C/v2/compute_friend_measures.py $D/measures/bubbliness.tab $D/friends-reduced.json $D/measures/friends-bubbliness.tab

python $C/v2/create_reciprocal_network.py $D/friends-reduced.json $D/reciprocal-friends-reduced.json
python $C/v2/compute_friend_measures.py $D/measures/pollution.tab $D/reciprocal-friends-reduced.json $D/measures/reciprocal-friends-pollution.tab
python $C/v2/compute_friend_measures.py $D/measures/partisanship.tab $D/reciprocal-friends-reduced.json $D/measures/reciprocal-friends-partisanship.tab
python $C/v2/compute_friend_measures.py $D/measures/ideology.tab $D/reciprocal-friends-reduced.json $D/measures/reciprocal-friends-ideology.tab
python $C/v2/compute_friend_measures.py $D/measures/bubbliness.tab $D/reciprocal-friends-reduced.json $D/measures/reciprocal-friends-bubbliness.tab

python $C/v2/combine_measures.py $D/all-measures.tab \
       "pollution\tfriends-pollution\treciprocal-friends-pollution\tpartisanship\tfriends-partisanship\treciprocal-friends-partisanship\tideology\tfriends-ideology\treciprocal-friends-ideology\tbubbliness\tfriends-bubbliness\treciprocal-friends-bubbliness" \
       $D/measures/pollution.tab $D/measures/friends-pollution.tab $D/measures/reciprocal-friends-pollution.tab \
       $D/measures/partisanship.tab $D/measures/friends-partisanship.tab $D/measures/reciprocal-friends-partisanship.tab \
       $D/measures/ideology.tab $D/measures/friends-ideology.tab $D/measures/reciprocal-friends-ideology.tab \
       $D/measures/bubbliness.tab $D/measures/friends-bubbliness.tab $D/measures/reciprocal-friends-bubbliness.tab
