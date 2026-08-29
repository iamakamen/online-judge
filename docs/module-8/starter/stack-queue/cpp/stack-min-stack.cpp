#include <bits/stdc++.h>
using namespace std;

int main() {
    int q;
    cin >> q;
    vector<long long> values;
    string operation;
    while (q--) {
        cin >> operation;
        if (operation == "push") {
            long long value;
            cin >> value;
            values.push_back(value);
        } else if (operation == "top" || operation == "min") {
            cout << "0\n";
        }

        // TODO: maintain stack values and answer top/min queries.
    }
}
