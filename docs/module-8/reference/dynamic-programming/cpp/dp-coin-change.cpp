#include <bits/stdc++.h>
using namespace std;int main(){int m,A;cin>>m>>A;vector<int>c(m),d(A+1,A+1);for(int&x:c)cin>>x;d[0]=0;for(int x=1;x<=A;x++)for(int v:c)if(v<=x)d[x]=min(d[x],d[x-v]+1);cout<<(d[A]>A?-1:d[A])<<'\n';}
