==========================
OpenBlock: Extra Packages
==========================

These are open-source packages originally released by the
EveryBlock.com team in 2009, but not actively used or maintained by
the OpenBlock core developers as of 2011.

Everything you actually want is probably in the
`main OpenBlock packages <http://openblockproject.org/docs/packages/>`_.

ebblog
------

The blog application used by http://blog.everyblock.com

Only of interest if you want to bundle a simple blog with your
OpenBlock site; you can probably ignore this.

For more information, see :doc:`ebblog`.


ebgeo
-----

The eb map system. This is mostly used for rendering and serving your
own map tiles with Mapnik, in case there is no suitable hosted map
solution for you.  OpenGeo Suite or TileMill might also be good solutions.

For more information, see :doc:`ebgeo`.


ebinternal
----------

Internal applications for the EveryBlock team.

Most OpenBlock users probably won't need this.
Not used by obdemo.

ebinternal consists of two apps, citypoll and feedback.  citypoll
powers EveryBlock's city voting system, both on EveryBlock.com and on
the iPhone app. feeback manages the feedback received from the
feedback forms at the bottom of almost every page on EveryBlock.com.

For more information, see :doc:`ebinternal`.



ebwiki
------

A basic wiki.

I'm not even sure if this is used on everyblock.com anymore.
Probably not useful to most OpenBlock users.

For more information, see :doc:`ebwiki`.


everyblock
----------

This package contains code/templates that are specific to
EveryBlock.com. They were released to fulfill the terms of the grant
that funded EveryBlock's development and are likely not of general
use, with the possible exception of scraper scripts in
everyblock/cities/ and everyblock/states/ which may at least be useful
as examples of how to write scrapers.

For more information, see :doc:`everyblock`.


Contents
========

.. toctree::
   :maxdepth: 1

   ebblog
   ebgeo
   ebinternal
   ebwiki
   everyblock


