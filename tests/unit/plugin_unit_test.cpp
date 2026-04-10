#include "ovx/gfx/plugin.hpp"

#include <cassert>

int main() {
    assert(ovx::gfx::plugin_name() == "ovx_gfx_plugin");
    return 0;
}
