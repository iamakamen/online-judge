#include <bits/stdc++.h>
using namespace std;int main(){int n;if(!(cin>>n))return 0;vector<long long>a(n),o(n,1);for(auto&x:a)cin>>x;long long p=1;for(int i=0;i<n;i++){o[i]=p;p*=a[i];}p=1;for(int i=n-1;i>=0;i--){o[i]*=p;p*=a[i];}for(int i=0;i<n;i++)cout<<o[i]<<(i+1==n?'\n':' ');}
