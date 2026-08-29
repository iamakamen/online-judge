#include <bits/stdc++.h>
using namespace std;int main(){int n;cin>>n;vector<long long>t;while(n--){long long x;cin>>x;auto i=lower_bound(t.begin(),t.end(),x);if(i==t.end())t.push_back(x);else *i=x;}cout<<t.size()<<'\n';}
