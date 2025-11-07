* [1. 前言](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0001.html)
* [2. 异构计算](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0002.html)
* 3. 功能调试
    * [3.1. 运行正常](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0004.html)
    * [3.2. 精度正常](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0005.html)
    * [3.3. 算子调试](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0006.html)
* 4. 性能分析
    * [4.1. 获取性能数据](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0008.html)
    * [4.2. 分析性能数据](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0009.html)
* 5. 性能优化
    * [5.1. 优化建议总览表](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_00010.html)
    * 5.2. 搬运优化
        * [5.2.1. 尽量一次搬运较大的数据块](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0013.html)
        * [5.2.2. GM地址尽量512B对齐](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0014.html)
        * [5.2.3. 高效的使用搬运API](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0015.html)
    * 5.3. 内存优化
        * [5.3.1. 算子与高阶API共享临时Buffer](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0017.html)
        * [5.3.2. 限制TilingData结构大小](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0018.html)
        * [5.3.3. 通过缩减Tensor ShapeInfo维度，优化栈空间](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0019.html)
        * [5.3.4. 通过Unified Buffer融合实现连续vector计算](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0020.html)
        * [5.3.5. 通过BT Buffer实现高效的bias计算](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0021.html)
        * [5.3.6. 通过FP Buffer存放量化参数实现高效随路量化](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0022.html)
        * [5.3.7. 通过L0C Buffer数据暂存实现高效的矩阵乘结果累加](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0023.html)
        * [5.3.8. 较小矩阵长驻L1 Buffer，仅分次搬运较大矩阵](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0024.html)
        * [5.3.9. 优化bank分配以提升读写性能](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0025.html)
    * 5.4. API使用优化
        * [5.4.1. 纯搬运类算子VECIN和VECOUT建议复用](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0027.html)
        * [5.4.2. 避免TPipe在对象内创建和初始化](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0028.html)
        * [5.4.3. Matmul使能AtomicAdd选项](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0029.html)
        * [5.4.4. Vector算子灵活运用Counter模式](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0030.html)
        * [5.4.5. 针对不同场景合理使用归约指令](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0031.html)
    * 5.5. 流水优化
        * [5.5.1. 使能double buffer](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0033.html)
        * [5.5.2. 使能Iterate或IterateAll异步接口避免AIC/AIV同步依赖](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0034.html)
    * 5.6. Tiling优化
        * [5.6.1. L2 Cache切分](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0036.html)
        * [5.6.2. 核间负载均衡](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0037.html)
* 6. 优秀实践
    * [6.1. FlashAttention算子性能调优案例](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0040.html)
    * [6.2. Matmul算子性能调优案例](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0041.html)
    * [6.3. GroupedMatmul算子性能调优案例](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0042.html)
    * [6.4. MC²算子性能调优案例](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_0043.html)
    * [6.5. Matmul高阶API使能IBShare性能提升案例](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_10000.html)
    * [6.6. Matmul常量化算子性能提升案例](https://www.hiascend.com/document/detail/zh/CANNCommunityEdition/82RC1/opdevg/ascendcbestP/atlas_ascendc_best_practices_10_10001.html)
