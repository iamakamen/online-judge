#include <bits/stdc++.h>
using namespace std;int main(){string s;cin>>s;int L=0,R=1;auto f=[&](int l,int r){while(l>=0&&r<(int)s.size()&&s[l]==s[r]){if(r-l+1>R-L){L=l;R=r+1;}--l;++r;}};for(int i=0;i<(int)s.size();i++){f(i,i);f(i,i+1);}cout<<s.substr(L,R-L)<<'\n';}
