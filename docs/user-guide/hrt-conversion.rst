HRT Conversion
==============

.. warning::

    Consult with your doctor about the accuracy of this tool before using it. 
    Ensure that you verified that the outputs are in fact correct before using.


This feature is designed to convert different serum measurements of Estradiol, Progesterone, Testosterone and Prolactin.
Now, the measurements used may be confusing, and here is an breakdown of the different measurements and their name meaning

+---------------------+-------------------------------------+----------------------------------------------------------------------------------------+
| Unit of Measurement |            Name Meaning             |                                    Reference Link                                      |
+=====================+=====================================+========================================================================================+
|       pmol/L        |         Picomoles Per Liter         |        https://www.nyp.org/healthlibrary/definitions/picomoles-per-liter-pmoll         |
+---------------------+-------------------------------------+----------------------------------------------------------------------------------------+
|        pg/mL        |      Picograms Per Milliliter       |      https://www.nyp.org/healthlibrary/definitions/picograms-per-milliliter-pgml       |
+---------------------+-------------------------------------+----------------------------------------------------------------------------------------+
|       nmol/L        |         Nanomoles Per Liter         |        https://www.nyp.org/healthlibrary/definitions/nanomoles-per-liter-nmoll         |
+---------------------+-------------------------------------+----------------------------------------------------------------------------------------+
|        ng/dL        |       Nanograms per deciliter       |       https://www.nyp.org/healthlibrary/definitions/nanograms-per-deciliter-ngdl       |
+---------------------+-------------------------------------+----------------------------------------------------------------------------------------+
|        mIU/L        | Milli-international Units Per Liter | https://www.nyp.org/healthlibrary/definitions/milli-international-units-per-liter-miul |
+---------------------+-------------------------------------+----------------------------------------------------------------------------------------+

Now we know what these measurements means, we can start breaking down how to use the commmand.
The command are divided into these subcommands:

- ``/hrt-convert estradiol``
- ``/hrt-convert testosterone``
- ``/hrt-convert progesterone``
- ``/hrt-convert prolactin``

These commands will always have these two inputs:

- ``amount`` - A number form of the amount of suggested unit to convert to
- ``unit`` - The unit to convert to. 

For the input ``unit``, there are two special cases:

1. If the command used is ``/hrt-convert estradiol``, then the only units that will be accepted are ``pmol/L`` and ``pg/mL``
2. For the command ``/hrt-convert progesterone``, the unit ``ng/dL`` is internally converted to ``ng/mL``.  I'm actually unsure of why, but if you think this is a mistake, please let me know.

And here is an example of how the output looks like. 

.. image:: /_assets/conversion_shot.png
    :alt: Example of HRT Conversion