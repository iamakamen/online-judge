#include <bits/stdc++.h>
using namespace std;int main(){int n;cin>>n;vector<int>a(n),o(n),s;for(int&x:a)cin>>x;for(int i=0;i<n;i++){while(!s.empty()&&a[s.back()]<a[i])o[s.back()]=i-s.back(),s.pop_back();s.push_back(i);}for(int i=0;i<n;i++)cout<<(i?" ":"")<<o[i];cout<<'\n';}
