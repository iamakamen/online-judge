#include <bits/stdc++.h>
using namespace std;int main(){int n;cin>>n;vector<long long>s;string t;while(n--){cin>>t;if(isdigit(t[0])||(t[0]=='-'&&t.size()>1))s.push_back(stoll(t));else{auto b=s.back();s.pop_back();auto a=s.back();s.pop_back();if(t=="+")s.push_back(a+b);if(t=="-")s.push_back(a-b);if(t=="*")s.push_back(a*b);if(t=="/")s.push_back(a/b);}}cout<<s.back()<<'\n';}
