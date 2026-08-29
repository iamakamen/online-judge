#include <bits/stdc++.h>
using namespace std;int main(){string s,t;cin>>s>>t;array<int,26>a{};for(char c:s)a[c-'a']++;for(char c:t)a[c-'a']--;cout<<(all_of(a.begin(),a.end(),[](int x){return x==0;})?"true":"false")<<'\n';}
