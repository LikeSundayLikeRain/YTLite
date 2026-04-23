ARCHS = arm64
TARGET := iphone:clang:16.5:13.0
DEBUG=0
FINALPACKAGE=1

include $(THEOS)/makefiles/common.mk

TWEAK_NAME = AABypass
$(TWEAK_NAME)_FILES = Bypass.x
$(TWEAK_NAME)_CFLAGS = -fobjc-arc

include $(THEOS_MAKE_PATH)/tweak.mk
