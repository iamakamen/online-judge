#include <bits/stdc++.h>
using namespace std;int main(){int n;cin>>n;long long p=0,q=0,x;while(n--){cin>>x;long long z=max(q,p+x);p=q;q=z;}cout<<q<<'\n';}
