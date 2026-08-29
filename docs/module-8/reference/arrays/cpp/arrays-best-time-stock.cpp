#include <bits/stdc++.h>
using namespace std; int main(){int n;cin>>n; long long x,lo=LLONG_MAX,b=0;while(n--){cin>>x;lo=min(lo,x);b=max(b,x-lo);}cout<<b<<'\n';}
