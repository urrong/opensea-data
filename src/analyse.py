import json
import diskcache as dc


if __name__ == '__main__':
    def main():
        persistent_cache = dc.Index("../db")

        # *** Count how many inverted keys are present ***
        # c, pp, i, cs = 0, 0, 0, len(persistent_cache)
        # prevk = None
        # for k in persistent_cache.keys():
        #     p = i / cs
        #     i += 1
        #     if p > pp:
        #         print(f"{p:.2%}", i, c)
        #         pp += 0.01
        #     if prevk is None:
        #         prevk = k
        #     else:
        #         if prevk < k:
        #             c += 1
        #         prevk = k
        # print(c)

        # *** Write first 100 records to JSON file ***
        data = {}
        for i, k in enumerate(persistent_cache.keys()):
            data[k] = persistent_cache[k]
            if i > 100:
                break
        with open("../data.json", "w") as f:
            json.dump(data, f, indent=4)
    main()
