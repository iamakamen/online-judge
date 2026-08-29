#include <bits/stdc++.h>
using namespace std;int main(){int n,e;cin>>n>>e;vector<int>z(n);for(int i=0;i<n;i++)cin>>z[i];if(n&&e>=0){int slow=0,fast=0;z[n-1]=e;bool ok=0;while(fast!=-1&&z[fast]!=-1){slow=z[slow];fast=z[z[fast]];if(slow==fast){ok=1;break;}}cout<<(ok?"true":"false");}else cout<<"false";cout<<'\n';}
