#include <bits/stdc++.h>
using namespace std; int main(){int n;cin>>n;set<long long>s;bool d=false;for(int i=0;i<n;i++){long long x;cin>>x;d|=!s.insert(x).second;}cout<<(d?"true":"false")<<'\n';}
