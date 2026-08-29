#include <bits/stdc++.h>
using namespace std;int main(){int n,m;cin>>n>>m;vector<long long>a(n+m);for(auto&x:a)cin>>x;sort(a.begin(),a.end());for(int i=0;i<n+m;i++)cout<<(i?" ":"")<<a[i];cout<<'\n';}
