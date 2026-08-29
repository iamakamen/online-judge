#include <bits/stdc++.h>
using namespace std;int main(){int n;cin>>n;long long a=1,b=1;while(n--)tie(a,b)=make_tuple(b,a+b);cout<<a<<'\n';}
