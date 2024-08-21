# add api key for 
API_KEY_0='sk-'
API_KEY_1='sk-'
API_KEY_2='sk-'
API_KEY_3='sk-'
API_KEY_4='sk-'
API_KEY_5='sk-'
API_KEY_6='sk-'
API_KEY_7='sk-'
API_KEY_8='sk-'
API_KEY_9='sk-'

zsh subrun.sh "0/0" $API_KEY_0 0 24 &
zsh subrun.sh "0/1" $API_KEY_1 25 49 &
zsh subrun.sh "0/2" $API_KEY_2 50 74 &
zsh subrun.sh "0/3" $API_KEY_3 75 99 &
zsh subrun.sh "0/4" $API_KEY_4 100 124 &
zsh subrun.sh "0/5" $API_KEY_5 125 149 &
zsh subrun.sh "0/6" $API_KEY_6 150 174 &
zsh subrun.sh "0/7" $API_KEY_7 175 199 &
zsh subrun.sh "0/8" $API_KEY_8 200 224 &
zsh subrun.sh "0/9" $API_KEY_9 225 250 &
wait




