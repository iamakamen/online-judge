#include <bits/stdc++.h>
using namespace std;

int main() {
    int n, m;
    cin >> n >> m;
    vector<int> first(n), second(m);
    for (auto& value : first) cin >> value;
    for (auto& value : second) cin >> value;

    // TODO: add the two reverse-digit serialized numbers.
    for (int i = 0; i < n; ++i) cout << (i ? " " : "") << first[i];
    cout << '\n';
}
