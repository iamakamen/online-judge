#include <bits/stdc++.h>
using namespace std; int main(){ios::sync_with_stdio(false);cin.tie(nullptr);int n; long long t; if(!(cin>>n>>t))return 0; unordered_map<long long,int> m; for(int i=0;i<n;i++){long long x;cin>>x;if(m.count(t-x)){cout<<m[t-x]<<' '<<i<<'\n';return 0;}m[x]=i;}}
