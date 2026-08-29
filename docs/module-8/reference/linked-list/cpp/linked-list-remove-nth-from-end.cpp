#include <bits/stdc++.h>
using namespace std;int main(){int n,k;cin>>n>>k;vector<long long>a(n);for(auto&x:a)cin>>x;a.erase(a.begin()+n-k);for(int i=0;i<(int)a.size();i++)cout<<(i?" ":"")<<a[i];cout<<'\n';}
