#include <bits/stdc++.h>
using namespace std;int main(){string s;cin>>s;vector<char>st;map<char,char>p={{')','('},{']','['},{'}','{'}};bool ok=1;for(char c:s)if(c=='('||c=='['||c=='{')st.push_back(c);else if(st.empty()||st.back()!=p[c])ok=0;else st.pop_back();cout<<((ok&&st.empty())?"true":"false")<<'\n';}
