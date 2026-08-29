#include <bits/stdc++.h>
using namespace std;int main(){int n;cin>>n;long long x,cur,best;cin>>cur;best=cur;for(int i=1;i<n;i++){cin>>x;cur=max(x,cur+x);best=max(best,cur);}cout<<best<<'\n';}
