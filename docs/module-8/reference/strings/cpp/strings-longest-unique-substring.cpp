#include <bits/stdc++.h>
using namespace std;int main(){string s;cin>>s;array<int,26>p; p.fill(-1);int l=0,a=0;for(int r=0;r<(int)s.size();r++){int c=s[r]-'a';l=max(l,p[c]+1);p[c]=r;a=max(a,r-l+1);}cout<<a<<'\n';}
