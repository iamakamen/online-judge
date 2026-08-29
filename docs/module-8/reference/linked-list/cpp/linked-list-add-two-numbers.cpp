#include <bits/stdc++.h>
using namespace std;int main(){int n,m;cin>>n>>m;vector<int>a(n),b(m),o;for(int&x:a)cin>>x;for(int&x:b)cin>>x;int c=0;for(int i=0;i<max(n,m);i++){int q=(i<n?a[i]:0)+(i<m?b[i]:0)+c;o.push_back(q%10);c=q/10;}if(c)o.push_back(c);for(int i=0;i<(int)o.size();i++)cout<<(i?" ":"")<<o[i];cout<<'\n';}
