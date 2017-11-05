#-------------------------------------------------
#
# Project created by QtCreator 2017-07-05T20:12:17
#
#-------------------------------------------------

QT       += core gui

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = FictionalUnits
TEMPLATE = app

CONFIG += c++11

SOURCES += source/main.cpp\
        source/mainwindow.cpp \
    source/funitssettings.cpp

HEADERS += source/mainwindow.h \
    source/funitssettings.h

FORMS += \
    source/mainwindow.ui

TRANSLATIONS += languages/funits_fi.ts

DISTFILES += \
    configuration/test.conf

DESTDIR = $$PWD
