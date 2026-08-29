#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;
    vector<long long> values(n);
    for (auto& value : values) cin >> value;

    // TODO: reverse the serialized linked list.
    for (int i = 0; i < n; ++i) cout << (i ? " " : "") << values[i];
    cout << '\n';
}
