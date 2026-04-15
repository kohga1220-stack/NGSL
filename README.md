# NGSL

NGSL: custom numerical grammar language with R-like data.frame and CSV support.

## Overview

NGSL is a custom numerical grammar language built on NumPy/SciPy. It supports data.frame-style data manipulation, CSV import/export, and R-like column access using both `df.V1` and `df$V1` syntax.

## Usage

1. Install Python 3.11 or later
2. Install the package in editable mode:
   ```bash
   pip install -e .
   ```
3. Run tests:
   ```bash
   pytest
   ```

## Features

- data.frame construction and column access
- read.csv / write.csv support with `header`, `sep`, and `row.names`
- basic statistical functions and matrix operations
- interpreter for a custom DSL with R-style syntax

## Plot files

This repository also contains generated plot files for data analysis:
- `achievement_vs_spresent.svg`
- `achievement_vs_sfeedpos.svg`
- `correlation_matrix.svg`
