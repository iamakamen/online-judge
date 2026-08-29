#include <bits/stdc++.h>
using namespace std;int main(){string s;int m;cin>>s>>m;vector<string>w(m);for(auto&z:w)cin>>z;vector<char>d(s.size()+1);d[0]=1;for(int i=0;i<(int)s.size();i++)if(d[i])for(auto&z:w)if(s.compare(i,z.size(),z)==0)d[i+z.size()]=1;cout<<(d.back()?"true":"false")<<'\n';}
