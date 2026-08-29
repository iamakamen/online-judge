#include <bits/stdc++.h>
using namespace std;int main(){int q;cin>>q;vector<long long>s;string op;while(q--){cin>>op;if(op=="push"){long long x;cin>>x;s.push_back(x);}else if(op=="pop")s.pop_back();else if(op=="top")cout<<s.back()<<'\n';else cout<<*min_element(s.begin(),s.end())<<'\n';}}
