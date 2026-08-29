#include <bits/stdc++.h>
using namespace std;int main(){int n,k;cin>>n>>k;vector<int>a(n);for(int&x:a)cin>>x;deque<int>d;for(int i=0;i<n;i++){while(!d.empty()&&d.front()<=i-k)d.pop_front();while(!d.empty()&&a[d.back()]<=a[i])d.pop_back();d.push_back(i);if(i>=k-1)cout<<(i==k-1?"":" ")<<a[d.front()];}cout<<'\n';}
