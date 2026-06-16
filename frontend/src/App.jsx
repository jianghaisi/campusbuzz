import React, { useEffect, useMemo, useState } from "react";
import {
  CalendarDays,
  Check,
  Clapperboard,
  Clipboard,
  ClipboardList,
  Copy,
  History,
  Image,
  Loader2,
  MessageCircle,
  Settings2,
  Sparkles,
  WandSparkles,
  X,
} from "lucide-react";
import { editImage, generateImage, generatePack, getConfig } from "./lib/api";

const initialForm = {
  shop_name: "星河奶茶",
  shop_type: "奶茶店",
  campaign: "新品芋泥麻薯奶茶，第二杯半价",
  audience: "大学生、女生、下午茶搭子",
  platform: "小红书",
  tone: "真实探店、宿舍姐妹分享",
  selling_points: "距离学校东门步行5分钟，有自习座位，拍照灯光好",
};

const imagePromptPresets = [
  {
    id: "polished_cover",
    title: "精修种草封面",
    tag: "小红书首图",
    description: "保留主体真实样子，提升光线、构图和质感。",
    prompt:
      "请基于上传图片中的主体进行精修，不要改变主体品类和核心外观。必须移除或替换原图中所有无关品牌、店名、Logo、杯身文字、包装文字和背景招牌；如果需要出现品牌文字，只能使用当前店铺名。根据主体类型自动优化：食物突出热气、色泽、摆盘和食欲；饮品突出杯身冷凝水、层次和清爽感；饰品突出材质、光泽、细节和佩戴/陈列氛围；其他商品突出真实质感和使用场景。画面适合小红书封面，明亮自然光，干净背景，有生活方式氛围，保留中文标题留白，不要夸张广告风。",
  },
  {
    id: "commercial_scene",
    title: "商业质感大片",
    tag: "活动海报",
    description: "更像商家宣传图，适合团购页、海报和活动页。",
    prompt:
      "请把上传图片中的主体做成高质感商业宣传图。主体必须仍然是原图里的物件，不要换成其他品类。必须移除或替换原图中所有无关品牌、店名、Logo、杯身文字、包装文字和背景招牌；如果需要出现品牌文字，只能使用当前店铺名。根据品类自动选择合适场景：饭菜使用温暖餐桌和诱人摆盘；饮品使用清爽桌面和自然光；小饰品使用柔和布景、微距细节和高级光泽；其他物件使用简洁陈列和品牌感背景。要求画面精致、真实、可用于本地生活商家推广。",
  },
  {
    id: "real_life_upgrade",
    title: "真实探店增强",
    tag: "学生实拍",
    description: "保留真实探店感，但让照片更干净、更好看。",
    prompt:
      "请在保留上传图片真实探店感的基础上优化画面。不要过度商业化，不要改变主体是什么。必须移除或替换原图中所有无关品牌、店名、Logo、杯身文字、包装文字和背景招牌；如果需要出现品牌文字，只能使用当前店铺名。根据主体自动处理：饭菜保留烟火气和份量感；饮品保留手持/桌面真实感；饰品保留细节和搭配感；其他物件保留真实使用场景。提升亮度、清晰度、构图和背景整洁度，让它像学生博主会发布的小红书图片。",
  },
];

function Field({ label, name, value, onChange, textarea = false, children }) {
  const Component = textarea ? "textarea" : "input";
  return (
    <label className="field">
      <span>{label}</span>
      {children || <Component name={name} value={value} onChange={onChange} rows={textarea ? 4 : undefined} />}
    </label>
  );
}

function Section({ icon: Icon, title, children, action }) {
  return (
    <section className="result-section">
      <div className="section-title">
        <div>
          <Icon size={18} />
          <h2>{title}</h2>
        </div>
        {action}
      </div>
      {children}
    </section>
  );
}

function CopyButton({ value }) {
  const [done, setDone] = useState(false);

  async function copy() {
    await navigator.clipboard.writeText(value);
    setDone(true);
    window.setTimeout(() => setDone(false), 1200);
  }

  return (
    <button className="icon-button" type="button" onClick={copy} title="复制">
      {done ? <Check size={16} /> : <Copy size={16} />}
    </button>
  );
}

function packToText(pack) {
  if (!pack) return "";
  return [
    `标题：\n${pack.titles.join("\n")}`,
    `种草笔记：\n${pack.note}`,
    `30秒脚本：\n${pack.video_script}`,
    `拍摄清单：\n${pack.shooting_checklist.join("、")}`,
    `评论回复：\n${pack.comment_replies.join("\n")}`,
    `KOC Brief：\n${pack.koc_brief}`,
  ].join("\n\n");
}

export default function App() {
  const [form, setForm] = useState(initialForm);
  const [config, setConfig] = useState(null);
  const [model, setModel] = useState("gpt-5.4-mini");
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [imageResult, setImageResult] = useState(null);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [uploadedPreview, setUploadedPreview] = useState("");
  const [promptModalOpen, setPromptModalOpen] = useState(false);
  const [selectedPresetId, setSelectedPresetId] = useState("polished_cover");
  const [customImagePrompt, setCustomImagePrompt] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [imageLoading, setImageLoading] = useState(false);

  useEffect(() => {
    getConfig()
      .then((data) => {
        setConfig(data);
        setModel(data.default_model || "gpt-5.4-mini");
      })
      .catch(() => {
        setConfig({
          default_model: "gpt-5.4-mini",
          image_model: "gpt-image-2",
          model_options: ["gpt-5.4-mini", "gpt-5.4", "gpt-5.2"],
          image_enabled: false,
          base_host: "未连接",
        });
      });

    const saved = window.localStorage.getItem("campusbuzz-history");
    if (saved) setHistory(JSON.parse(saved));
  }, []);

  const canSubmit = useMemo(
    () => form.shop_name && form.shop_type && form.campaign && form.audience,
    [form]
  );

  const pack = result?.pack;
  const selectedPreset = imagePromptPresets.find((item) => item.id === selectedPresetId) || imagePromptPresets[0];
  const coverImage =
    imageResult?.image_url || (imageResult?.b64_json ? `data:image/png;base64,${imageResult.b64_json}` : "");

  function updateField(event) {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  }

  function saveHistory(item) {
    const next = [item, ...history].slice(0, 8);
    setHistory(next);
    window.localStorage.setItem("campusbuzz-history", JSON.stringify(next));
  }

  function updateUploadedImage(event) {
    const file = event.target.files?.[0];
    if (!file) return;
    setUploadedImage(file);
    setUploadedPreview(URL.createObjectURL(file));
    setImageResult(null);
  }

  function buildFinalImagePrompt() {
    const context = [
      `当前店铺名：${form.shop_name}`,
      `店铺类型：${form.shop_type}`,
      `活动/产品：${form.campaign}`,
      `目标人群：${form.audience}`,
      `补充卖点：${form.selling_points || "无"}`,
    ].join("。");
    const brandRule = `品牌规则：成品图中不得出现任何与当前店铺无关的品牌、店名、Logo 或包装文字。若上传图里有其他品牌，例如古茗、喜茶、蜜雪冰城等，必须删除或替换为“${form.shop_name}”。如果文字渲染不稳定，宁可使用无字干净杯身/包装，也不要保留错误品牌。`;
    const basePrompt = customImagePrompt.trim() || selectedPreset.prompt;
    return `${context}。\n${brandRule}\n${basePrompt}`;
  }

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");
    setImageResult(null);
    try {
      const data = await generatePack({ ...form, model });
      setResult(data);
      saveHistory({
        id: Date.now(),
        shop_name: form.shop_name,
        campaign: form.campaign,
        model: data.model,
        pack: data.pack,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function createImage() {
    setImageLoading(true);
    setError("");
    try {
      const prompt = buildFinalImagePrompt();
      const data = uploadedImage
        ? await editImage({
            file: uploadedImage,
            prompt,
            model: config?.image_model || "gpt-image-2",
            size: "1024x1024",
          })
        : await generateImage({
            prompt: pack?.cover_prompt ? `${pack.cover_prompt}\n${prompt}` : prompt,
            model: config?.image_model || "gpt-image-2",
            size: "1024x1024",
          });
      setImageResult(data);
      setPromptModalOpen(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setImageLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <div className="workspace">
        <aside className="brief-panel">
          <div className="brand-mark">
            <Sparkles size={22} />
            <div>
              <strong>CampusBuzz AI</strong>
              <span>校园本地生活内容 Copilot</span>
            </div>
          </div>

          <div className="settings-strip">
            <div>
              <Settings2 size={16} />
              <span>{config?.base_host || "加载配置中"}</span>
            </div>
            <strong>{config?.image_model || "gpt-image-2"}</strong>
          </div>

          <form onSubmit={submit} className="brief-form">
            <Field label="内容模型">
              <select value={model} onChange={(event) => setModel(event.target.value)}>
                {(config?.model_options || ["gpt-5.4-mini"]).map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </Field>
            <Field label="店铺名" name="shop_name" value={form.shop_name} onChange={updateField} />
            <Field label="店铺类型" name="shop_type" value={form.shop_type} onChange={updateField} />
            <Field label="活动或新品" name="campaign" value={form.campaign} onChange={updateField} textarea />
            <Field label="目标人群" name="audience" value={form.audience} onChange={updateField} />
            <Field label="平台" name="platform" value={form.platform} onChange={updateField} />
            <Field label="内容风格" name="tone" value={form.tone} onChange={updateField} />
            <Field label="补充卖点" name="selling_points" value={form.selling_points} onChange={updateField} textarea />

            <button className="generate-button" disabled={!canSubmit || loading}>
              {loading ? <Loader2 className="spin" size={18} /> : <WandSparkles size={18} />}
              {loading ? "生成中" : "生成内容包"}
            </button>
            {error && <p className="error-text">{error}</p>}
          </form>

          <div className="history-panel">
            <div className="mini-title">
              <History size={15} />
              <span>最近生成</span>
            </div>
            {history.length === 0 && <p>暂无历史记录</p>}
            {history.map((item) => (
              <button
                type="button"
                key={item.id}
                onClick={() => setResult({ model: item.model, pack: item.pack })}
                className="history-item"
              >
                <strong>{item.shop_name}</strong>
                <span>{item.campaign}</span>
              </button>
            ))}
          </div>
        </aside>

        <section className="output-panel">
          <header className="output-header">
            <p>本地生活种草工作台</p>
            <h1>从一次门店活动，生成图文、短视频脚本、拍摄 brief 和封面图。</h1>
          </header>

          {!pack && (
            <div className="empty-state">
              <Clapperboard size={44} />
              <p>填写左侧 brief 后生成首版内容包。默认样例适合奶茶店新品活动。</p>
            </div>
          )}

          {pack && (
            <div className="result-grid">
              <Section icon={Sparkles} title={`标题 · ${result.model}`} action={<CopyButton value={pack.titles.join("\n")} />}>
                <div className="title-list">
                  {pack.titles.map((title) => (
                    <span key={title}>{title}</span>
                  ))}
                </div>
              </Section>

              <Section icon={ClipboardList} title="种草笔记" action={<CopyButton value={pack.note} />}>
                <p className="long-copy">{pack.note}</p>
              </Section>

              <Section icon={Clapperboard} title="30 秒脚本" action={<CopyButton value={pack.video_script} />}>
                <p className="long-copy">{pack.video_script}</p>
              </Section>

              <Section icon={CalendarDays} title="分镜">
                <div className="shot-list">
                  {pack.shots.map((shot, index) => (
                    <article key={`${shot.scene}-${index}`}>
                      <strong>{shot.scene}</strong>
                      <p>{shot.camera}</p>
                      <span>{shot.caption || shot.copy}</span>
                    </article>
                  ))}
                </div>
              </Section>

              <Section icon={Clipboard} title="KOC Brief" action={<CopyButton value={pack.koc_brief} />}>
                <p className="long-copy">{pack.koc_brief}</p>
              </Section>

              <Section icon={Image} title="封面图">
                <label className="upload-box">
                  <input type="file" accept="image/*" onChange={updateUploadedImage} />
                  {uploadedPreview ? (
                    <img src={uploadedPreview} alt="上传的参考图" />
                  ) : (
                    <span>上传一张产品图，可用于改图。支持奶茶、饭菜、饰品或其他物件。</span>
                  )}
                </label>
                <div className="image-box">
                  {coverImage ? <img src={coverImage} alt="AI 生成封面" /> : <p>{pack.cover_prompt}</p>}
                </div>
                <div className="image-actions">
                  <button className="secondary-button" type="button" onClick={() => setPromptModalOpen(true)} disabled={imageLoading}>
                    {imageLoading ? <Loader2 className="spin" size={16} /> : <Image size={16} />}
                    {imageLoading ? "生成图片中" : uploadedImage ? "选择提示词并改图" : "选择提示词生成封面"}
                  </button>
                  <CopyButton value={buildFinalImagePrompt()} />
                </div>
              </Section>

              <Section icon={ClipboardList} title="拍摄清单">
                <ul className="compact-list">
                  {pack.shooting_checklist.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </Section>

              <Section icon={MessageCircle} title="评论回复">
                <ul className="compact-list">
                  {pack.comment_replies.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </Section>

              <Section icon={Sparkles} title="角度变体" action={<CopyButton value={packToText(pack)} />}>
                <div className="variant-row">
                  {pack.variants.map((item) => (
                    <span key={item}>{item}</span>
                  ))}
                </div>
                <p className="conversion">{pack.conversion_hook}</p>
              </Section>
            </div>
          )}
        </section>
      </div>

      {promptModalOpen && (
        <div className="modal-backdrop" role="dialog" aria-modal="true">
          <div className="prompt-modal">
            <div className="modal-head">
              <div>
                <p>{uploadedImage ? "基于上传图片改图" : "生成一张新封面图"}</p>
                <h2>选择图片提示词</h2>
              </div>
              <button className="icon-button" type="button" onClick={() => setPromptModalOpen(false)} title="关闭">
                <X size={16} />
              </button>
            </div>

            <div className="prompt-card-grid">
              {imagePromptPresets.map((preset) => (
                <button
                  className={`prompt-card ${selectedPresetId === preset.id ? "selected" : ""}`}
                  type="button"
                  key={preset.id}
                  onClick={() => {
                    setSelectedPresetId(preset.id);
                    setCustomImagePrompt("");
                  }}
                >
                  <span>{preset.tag}</span>
                  <strong>{preset.title}</strong>
                  <p>{preset.description}</p>
                </button>
              ))}
            </div>

            <label className="field">
              <span>自定义提示词</span>
              <textarea
                rows={5}
                value={customImagePrompt}
                onChange={(event) => setCustomImagePrompt(event.target.value)}
                placeholder={`可留空使用「${selectedPreset.title}」。也可以写：保留原图主体，把背景换成校园桌面，提升光线和质感。`}
              />
            </label>

            <div className="prompt-preview">
              <strong>将发送给图片模型的提示词</strong>
              <p>{buildFinalImagePrompt()}</p>
            </div>

            <div className="modal-actions">
              <button className="secondary-button" type="button" onClick={() => setPromptModalOpen(false)}>
                取消
              </button>
              <button className="generate-button" type="button" onClick={createImage} disabled={imageLoading}>
                {imageLoading ? <Loader2 className="spin" size={18} /> : <WandSparkles size={18} />}
                {imageLoading ? "生成中" : uploadedImage ? "开始改图" : "生成封面"}
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
